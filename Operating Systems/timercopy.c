#include "devices/timer.h"
#include <debug.h>
#include <inttypes.h>
#include <round.h>
#include <stdio.h>
#include "devices/pit.h"
#include "threads/interrupt.h"
#include "threads/synch.h"
#include "threads/thread.h"

/* See [8254] for hardware details of the 8254 timer chip. */

#if TIMER_FREQ < 19
#error 8254 timer requires TIMER_FREQ >= 19
#endif
#if TIMER_FREQ > 1000
#error TIMER_FREQ <= 1000 recommended
#endif

/* Number of timer ticks since OS booted. */
static int64_t ticks;

// begin Elena's code

/* The current load average. */
static fixed_point_t system_load_avg;

// end Elena's code

/* Number of loops per timer tick.
   Initialized by timer_calibrate(). */
static unsigned loops_per_tick;

/* List of sleeping threads. */
static struct list sleeping_list;

static intr_handler_func timer_interrupt;
static list_less_func wakeup_list_less;
static bool too_many_loops (unsigned loops);
static void busy_wait (int64_t loops);
static void real_time_sleep (int64_t num, int32_t denom);
static void real_time_delay (int64_t num, int32_t denom);


/* Sets up the timer to interrupt TIMER_FREQ times per second,
   and registers the corresponding interrupt. */
void
timer_init (void)
{
  pit_configure_channel (0, 2, TIMER_FREQ);
  intr_register_ext (0x20, timer_interrupt, "8254 Timer");
  list_init (&sleeping_list);
  system_load_avg = fix_int(0); // ELena's addition
}

/* Calibrates loops_per_tick, used to implement brief delays. */
void
timer_calibrate (void)
{
  unsigned high_bit, test_bit;

  ASSERT (intr_get_level () == INTR_ON);
  printf ("Calibrating timer...  ");

  /* Approximate loops_per_tick as the largest power-of-two
     still less than one timer tick. */
  loops_per_tick = 1u << 10;
  while (!too_many_loops (loops_per_tick << 1))
    {
      loops_per_tick <<= 1;
      ASSERT (loops_per_tick != 0);
    }

  /* Refine the next 8 bits of loops_per_tick. */
  high_bit = loops_per_tick;
  for (test_bit = high_bit >> 1; test_bit != high_bit >> 10; test_bit >>= 1)
    if (!too_many_loops (high_bit | test_bit))
      loops_per_tick |= test_bit;

  printf ("%'"PRIu64" loops/s.\n", (uint64_t) loops_per_tick * TIMER_FREQ);
}

/* Returns the number of timer ticks since the OS booted. */
int64_t
timer_ticks (void)
{
  enum intr_level old_level = intr_disable ();
  int64_t t = ticks;
  intr_set_level (old_level);
  return t;
}

/* Returns the number of timer ticks elapsed since THEN, which
   should be a value once returned by timer_ticks(). */
int64_t
timer_elapsed (int64_t then)
{
  return timer_ticks () - then;
}

/* Sleeps for approximately TICKS timer ticks.  Interrupts must
   be turned on. */
void
timer_sleep (int64_t ticks)
{
  int64_t start = timer_ticks ();

  ASSERT (intr_get_level () == INTR_ON);
  if (ticks <= 0) {
    return;
  }
  enum intr_level old_level = intr_disable ();
  struct thread *t = thread_current ();
  list_remove (&t ->elem);
  t ->wakeup = start + ticks;
  list_insert_ordered (&sleeping_list, &t ->sleepelem, &wakeup_list_less, NULL);
  thread_block ();
  intr_set_level (old_level);
}

/* Sleeps for approximately MS milliseconds.  Interrupts must be
   turned on. */
void
timer_msleep (int64_t ms)
{
  real_time_sleep (ms, 1000);
}

/* Sleeps for approximately US microseconds.  Interrupts must be
   turned on. */
void
timer_usleep (int64_t us)
{
  real_time_sleep (us, 1000 * 1000);
}

/* Sleeps for approximately NS nanoseconds.  Interrupts must be
   turned on. */
void
timer_nsleep (int64_t ns)
{
  real_time_sleep (ns, 1000 * 1000 * 1000);
}

/* Busy-waits for approximately MS milliseconds.  Interrupts need
   not be turned on.
   Busy waiting wastes CPU cycles, and busy waiting with
   interrupts off for the interval between timer ticks or longer
   will cause timer ticks to be lost.  Thus, use timer_msleep()
   instead if interrupts are enabled. */
void
timer_mdelay (int64_t ms)
{
  real_time_delay (ms, 1000);
}

/* Sleeps for approximately US microseconds.  Interrupts need not
   be turned on.
   Busy waiting wastes CPU cycles, and busy waiting with
   interrupts off for the interval between timer ticks or longer
   will cause timer ticks to be lost.  Thus, use timer_usleep()
   instead if interrupts are enabled. */
void
timer_udelay (int64_t us)
{
  real_time_delay (us, 1000 * 1000);
}

/* Sleeps execution for approximately NS nanoseconds.  Interrupts
   need not be turned on.
   Busy waiting wastes CPU cycles, and busy waiting with
   interrupts off for the interval between timer ticks or longer
   will cause timer ticks to be lost.  Thus, use timer_nsleep()
   instead if interrupts are enabled.*/
void
timer_ndelay (int64_t ns)
{
  real_time_delay (ns, 1000 * 1000 * 1000);
}

/* Prints timer statistics. */
void
timer_print_stats (void)
{
  printf ("Timer: %"PRId64" ticks\n", timer_ticks ());
}

/* new function! This increments the curr_cpu of only the
running thread, and updates thats thread's priority. */
// begin Elena's code
void
increment_curr_cpu (void)
{
  fixed_point_t before_cpu = thread_current()->recent_cpu; //need to fix!
      //printf("before cpu: %d\n", fix_round(before_cpu));

  fixed_point_t new_cpu = fix_add(before_cpu, fix_int(1));
    //printf("current cpu: %d\n", fix_round(new_cpu));

}

/* new function! updates the load_avg value used in the
Advanced Scheduler. Returns nothing.
*/
void
update_load_avg (void)
{
  // use my getter function to get size of list of ready threads
  fixed_point_t ready_threads = fix_int((int) ready_thread_amount());
  //printf("ready threads are %d\n", fix_round(fix_mul(fix_int(1000), ready_threads)));

  fixed_point_t curr_load_avg = system_load_avg;
  //printf("curr load average is %d\n", fix_round(fix_mul(fix_int(1000), curr_load_avg)));

  // math function
  fixed_point_t new_load_avg = fix_add(fix_mul(fix_frac(59,60), curr_load_avg), fix_mul(fix_frac(1,60), ready_threads));
  // overwrite old load average
  system_load_avg = new_load_avg;
   // printf("new load average is %d\n", fix_round(fix_mul(fix_int(1000), new_load_avg)));
  update_average_in_threads(system_load_avg);

}

void
update_recent_cpu(struct thread *t)
{
  //long equation from spec
  fixed_point_t new_cpu =
     fix_add(fix_mul(fix_div(fix_mul(fix_int(2), system_load_avg), fix_add(fix_mul(fix_int(2),
        system_load_avg), fix_int(1))), t->recent_cpu), fix_int(t->niceness));

  //setting the cpu
  t->recent_cpu = new_cpu;
}

void
update_priority_mlfqs(struct thread *t) {
  // long equation from spec
  fixed_point_t new_priority = fix_sub(fix_sub(fix_int(PRI_MAX),fix_div(t->recent_cpu, fix_int(4))), fix_mul(fix_int(t->niceness), fix_int(2)));

  // truncating it to fall within the priority range [0, 63]
  int new_priority_rounded = fix_round(new_priority);
  if (new_priority_rounded > PRI_MAX) new_priority_rounded = PRI_MAX;
  else if (new_priority_rounded < PRI_MIN) new_priority_rounded = PRI_MIN;

  //setting the priority
  t->priority = new_priority_rounded;

}

void
update_all_priorities(int todo)
{
  if (todo == 0)
  {
    // only update the priority of the running thread.
    update_priority_mlfqs(thread_current());

  }
  else if (todo == 1)
  {
    // for every thread update their recent_cpu
    thread_foreach(update_recent_cpu, NULL);

    // for every thread update their priority
    thread_foreach(update_priority_mlfqs, NULL);
  }
}
//end Elena's code



/* Timer interrupt handler. */
static void
timer_interrupt (struct intr_frame *args UNUSED)
{
  ticks++;
  thread_tick ();
    //begin Elena's code
  // make sure to run with pintos -v --gdb -- -q -mlfqs run mlfqs-recent-1
  if(thread_mlfqs) {
    increment_curr_cpu(); //done
    //enum intr_level old_level;
    //old_level = intr_disable ();

    // int are_we_multiple_4 = 0;
    // int are_we_multiple_100 = 0;

    //printf("%d; %d\n", advanced_ticks, TIMER_FREQ);

    //printf("advanced ticks over four: %d; advanced ticks over 100: %d\n", fix_trunc(tt4), fix_trunc(tt100));
    //printf("are we mul of 4 or 100? %d; %d\n", are_we_multiple_4, are_we_multiple_100);

    //intr_disable();
      if (timer_ticks() % 4 ==0 && timer_ticks() % TIMER_FREQ == 0)
    {
      //are_we_multiple_4 = 0;
      //are_we_multiple_100 = 0;
      update_load_avg();
      update_all_priorities(1);
    }
    //else if((are_we_multiple_4 == 1)) {
    else if (timer_ticks() % 4 ==0) {

      //are_we_multiple_4 = 0;

      update_all_priorities(0); // need to do
    }
    //intr_enable();
    //intr_set_level (old_level);
  }
    //end Elena's code

  struct list_elem *t_elem = list_begin (&sleeping_list);
  while (t_elem != list_end (&sleeping_list) && !list_empty(&sleeping_list)) {
    struct thread *t = list_entry (t_elem, struct thread, sleepelem);
    if (t ->wakeup > ticks) { // check wakeup time to global
      break;
    }
    // otherwise, if the thread should have woken up by now
    list_remove (t_elem); // take the thread off the sleeping list
    thread_unblock (t); // unblock and put back on ready_list

    if (t ->priority > thread_current ()-> priority) {
      // thread_yield ();
    }

    t_elem = list_begin (&sleeping_list); // update to elem with next min wakeup time
  }

}


/* Returns true if LOOPS iterations waits for more than one timer
   tick, otherwise false. */
static bool
too_many_loops (unsigned loops)
{
  /* Wait for a timer tick. */
  int64_t start = ticks;
  while (ticks == start)
    barrier ();

  /* Run LOOPS loops. */
  start = ticks;
  busy_wait (loops);

  /* If the tick count changed, we iterated too long. */
  barrier ();
  return start != ticks;
}

/* Iterates through a simple loop LOOPS times, for implementing
   brief delays.
   Marked NO_INLINE because code alignment can significantly
   affect timings, so that if this function was inlined
   differently in different places the results would be difficult
   to predict. */
static void NO_INLINE
busy_wait (int64_t loops)
{
  while (loops-- > 0)
    barrier ();
}

/* Sleep for approximately NUM/DENOM seconds. */
static void
real_time_sleep (int64_t num, int32_t denom)
{
  /* Convert NUM/DENOM seconds into timer ticks, rounding down.
        (NUM / DENOM) s
     ---------------------- = NUM * TIMER_FREQ / DENOM ticks.
     1 s / TIMER_FREQ ticks
  */
  int64_t ticks = num * TIMER_FREQ / denom;

  ASSERT (intr_get_level () == INTR_ON);
  if (ticks > 0)
    {
      /* We're waiting for at least one full timer tick.  Use
         timer_sleep() because it will yield the CPU to other
         processes. */
      timer_sleep (ticks);
    }
  else
    {
      /* Otherwise, use a busy-wait loop for more accurate
         sub-tick timing. */
      real_time_delay (num, denom);
    }
}

/* Busy-wait for approximately NUM/DENOM seconds. */
static void
real_time_delay (int64_t num, int32_t denom)
{
  /* Scale the numerator and denominator down by 1000 to avoid
     the possibility of overflow. */
  ASSERT (denom % 1000 == 0);
  busy_wait (loops_per_tick * num / 1000 * TIMER_FREQ / (denom / 1000));
}

/* Compare two alarm wakeup times */
static bool
wakeup_list_less (const struct list_elem *a, const struct list_elem *b, void *aux UNUSED)
{
  struct thread *t_a = list_entry(a, struct thread, elem);
  struct thread *t_b = list_entry(b, struct thread, elem);
  return (t_a ->wakeup < t_b ->wakeup);
}

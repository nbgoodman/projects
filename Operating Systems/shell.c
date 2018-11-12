#include <ctype.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <signal.h>
#include <sys/wait.h>
#include <termios.h>
#include <unistd.h>

#include "tokenizer.h"

/* Convenience macro to silence compiler warnings about unused function parameters. */
#define unused __attribute__((unused))

/* Whether the shell is connected to an actual terminal or not. */
bool shell_is_interactive;

/* File descriptor for the shell input */
int shell_terminal;

/* Terminal mode settings for the shell */
struct termios shell_tmodes;

/* Process group id for the shell */
pid_t shell_pgid;

int cmd_exit(struct tokens *tokens);
int cmd_help(struct tokens *tokens);
int cmd_pwd(struct tokens *tokens);
int cmd_cd(struct tokens *tokens);

/* Built-in command functions take token array (see parse.h) and return int */
typedef int cmd_fun_t(struct tokens *tokens);

/* Built-in command struct and lookup table */
typedef struct fun_desc {
  cmd_fun_t *fun;
  char *cmd;
  char *doc;
} fun_desc_t;

fun_desc_t cmd_table[] = {
  {cmd_help, "?", "show this help menu"},
  {cmd_exit, "exit", "exit the command shell"},
  {cmd_pwd, "pwd", "print working directory"},
  {cmd_cd, "cd", "changes working directory"}
};

/* Prints a helpful description for the given command */
int cmd_help(unused struct tokens *tokens) {
  for (unsigned int i = 0; i < sizeof(cmd_table) / sizeof(fun_desc_t); i++)
    printf("%s - %s\n", cmd_table[i].cmd, cmd_table[i].doc);
  return 1;
}

/* Exits this shell */
int cmd_exit(unused struct tokens *tokens) {
  exit(0);
}

/* Prints current directory */
int cmd_pwd(unused struct tokens *tokens) {
  long size;
  char *buf;
  char *ptr;
  size = pathconf(".", _PC_PATH_MAX);
  if ((buf = (char *)malloc((size_t)size)) != NULL) {
    ptr = getcwd(buf, (size_t)size);
    fprintf(stdout, "%s\n", ptr);
    free(buf);
  }
  else {
    perror("getcwd() error");
  }
   return 0;
}

int cmd_cd(unused struct tokens *tokens) {
  int worked;
  char * directory = tokens_get_token(tokens, 1);
  if (directory) {
    worked = chdir(directory);
    if (worked == -1) {
      fprintf(stdout, "Invalid Directory\n");
    }
  }
  else {
    fprintf(stdout, "No Directory Entered\n");
  }
  return 0;
}
/* Looks up the built-in command, if it exists. */
int lookup(char cmd[]) {
  for (unsigned int i = 0; i < sizeof(cmd_table) / sizeof(fun_desc_t); i++)
    if (cmd && (strcmp(cmd_table[i].cmd, cmd) == 0))
      return i;
  return -1;
}
/* from https://stackoverflow.com/questions/8465006/how-do-i-concatenate-two-strings-in-c */
char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1)+strlen(s2)+1);//+1 for the zero-terminator
    //in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}

char* check_in_path (char* program) {
  int inpath;
  char* path_tokens = strtok(getenv("PATH"), ":");
  while(path_tokens != NULL) {
    char* pathback = concat(path_tokens, "/");
    char* fullpath = concat(pathback, program);
    inpath = access(fullpath, F_OK);
    if (inpath == 0) {
      return fullpath;
    }
    path_tokens = strtok(NULL, ":");
  }
  return program;
}
/* Intialization procedures for this shell */
void init_shell() {
  /* Our shell is connected to standard input. */
  shell_terminal = STDIN_FILENO;

  /* Check if we are running interactively */
  shell_is_interactive = isatty(shell_terminal);

  if (shell_is_interactive) {
    /* If the shell is not currently in the foreground, we must pause the shell until it becomes a
     * foreground process. We use SIGTTIN to pause the shell. When the shell gets moved to the
     * foreground, we'll receive a SIGCONT. */
    while (tcgetpgrp(shell_terminal) != (shell_pgid = getpgrp()))
      kill(-shell_pgid, SIGTTIN);

    /* Saves the shell's process id */
    shell_pgid = getpid();

    /* Take control of the terminal */
    tcsetpgrp(shell_terminal, shell_pgid);

    /* Save the current termios to a variable, so it can be restored later. */
    tcgetattr(shell_terminal, &shell_tmodes);
  }
}

int main(unused int argc, unused char *argv[]) {
  init_shell();
  static char line[4096];
  int line_num = 0;

  /* Please only print shell prompts when standard input is not a tty */
  if (shell_is_interactive)
    fprintf(stdout, "%d: ", line_num);

  while (fgets(line, 4096, stdin)) {
    /* Split our line into words. */
    struct tokens *tokens = tokenize(line);

    /* Find which built-in function to run. */
    int fundex = lookup(tokens_get_token(tokens, 0));

    if (fundex >= 0) {
      cmd_table[fundex].fun(tokens);
    }
    else {
      pid_t pid = fork();
      if (pid == 0) {
        pid_t child_pid = getpid();
        unused int newgroup = setpgid(child_pid, child_pid);
        unused int newforeground = tcsetpgrp(0, child_pid);
        char* filename;
        FILE *fd;
        int filein = 0;
        int fileout = 0;
        int ret;
        const char* less = "<";
        const char* more = ">";
        size_t length = tokens_get_length(tokens);
        char** args = malloc((length + 1) * sizeof(char*));
        args[length] = NULL;
        printf("get here");
        char* program = tokens_get_token(tokens, 0);
        char* realprogram = check_in_path(program);
        for (int i = 0; i < length; i++) {
          char* curtoken = tokens_get_token(tokens, i);
          if (strcmp(curtoken, less) == 0) {
            filein = 1;
          }
          else if (strcmp(curtoken, more) == 0) {
            fileout = 1;
          }
          else if (filein == 1 || fileout == 1) {
            filename = curtoken;
            char** newargs = realloc(args, (length - 1) * sizeof(char*));
            if (newargs == NULL) {
              perror("Realloc failed");
            }
            args = newargs;
            args[length - 2] = NULL;
          }
          else {
            args[i] = tokens_get_token(tokens, i);
          }
        }
        if (filein == 1) {
          fd = fopen(filename, "r");
          int filenum = fileno(fd);
          dup2(filenum, 0);
          fclose(fd);
        }
        if (fileout == 1) {
          fd = fopen(filename, "w");
          int filenum = fileno(fd);
          dup2(filenum, 1);
          fclose(fd);
        }
        ret = execv(realprogram, args);
        if (ret == -1) {
          perror(realprogram);
        }
        free(args);
        exit(0);
      }
      if (pid != 0) {
        int status;
        wait(&status);
      }
    }

    if (shell_is_interactive)
      /* Please only print shell prompts when standard input is not a tty */
      fprintf(stdout, "%d: ", ++line_num);

    /* Clean up memory */
    tokens_destroy(tokens);
  }

  return 0;
}

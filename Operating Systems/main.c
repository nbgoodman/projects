#include <stdio.h>
#include <sys/resource.h>

int main() {
    struct rlimit r1;
    getrlimit(RLIMIT_STACK, &r1);
    printf("stack size: %lld\n", (long long int) r1.rlim_cur);
    getrlimit(RLIMIT_NPROC, &r1);
    printf("process limit: %lld\n", (long long int) r1.rlim_cur);
    getrlimit(RLIMIT_NOFILE, &r1);
    printf("max file descriptors: %lld\n", (long long int) r1.rlim_cur);
    return 0;
}

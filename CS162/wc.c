#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
int main(int argc, char *argv[]) {
  int c;
  if (argv[1]) {
    FILE *input_file;
    char *input = argv[1];
    input_file = fopen(input, "r");
  }
  int wordcount = 0;
  int lettercount = 0;
  int linecount = 0;
  int prevletter = -5;
  int found_word = 0;
  if (argv[1] != NULL) {
    FILE *input_file;
    char *input = argv[1];
    input_file = fopen(input, "r");
    while ((c = fgetc(input_file)) != -1)
    {
      if (prevletter != -5) {
        if ((prevletter == ' ' || prevletter == '\n')  &&  (char) c != ' ' &&  (char) c != '\n' && (char) c != '\r') {
          wordcount += 1;
        }
        if (c == '\n') {
          linecount += 1;
        }
      }
      else {
        if ((char) c != ' ' && (char) c != '\n' && (char) c != '\r') {
          wordcount += 1;
        }
        if ((char) c == '\n') {
          linecount += 1;
        }
      }
      prevletter = (char) c;
      lettercount += 1;
      }
    fclose(input_file);
    printf(" %i %i %i %s \n", linecount, wordcount, lettercount, argv[1]);
  }
  else {
    size_t bufsize = 32;

    char *buffer = malloc(bufsize * sizeof(char));
    if(buffer == NULL)
    {
        perror("Unable to allocate buffer");
        exit(1);
    }
    getdelim(&buffer, &bufsize, -1, stdin);
    int a = 0;
    while ((c = buffer[a]) != 0)  {
      if (prevletter != -5) {
        if ((prevletter == ' ' || prevletter == '\n')  &&  (char) c != ' ' &&  (char) c != '\n' && (char) c != '\r') {
          wordcount += 1;
        }
        if (c == '\n') {
          linecount += 1;
        }
      }
      else {
        if ((char) c != ' ' && (char) c != '\n' && (char) c != '\r') {
          wordcount += 1;
        }
        if ((char) c == '\n') {
          linecount += 1;
        }
      }
      prevletter = (char) c;
      lettercount += 1;
      a += 1;
      }
    printf(" %i %i %i \n", linecount, wordcount, lettercount);
    free(buffer);
  }

  return 0;
}

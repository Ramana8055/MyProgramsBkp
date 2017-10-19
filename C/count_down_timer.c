#include <stdio.h>
#include <time.h>

int main()
{
   time_t start = time(NULL);

   while (1) {
      if ((time(NULL) - start) >= 10) {
         printf("timedout\n");
         return 0;
      }
   }
}

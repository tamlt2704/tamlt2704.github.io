# 1. Getting started
## 1.1 Starting prolog

Starting prolog generally produce a number of lines of heading followed by a
line containing just

```shell
swipl
```

![alt prolog](https://github.com/tamlt2704/tamlt2704.github.io/blob/master/pages/assets/proglog/1_start_prolog.JPG "swipl")

Hello world

```prolog
?-write('Hello world'),nl,write('Welcome to Prolog'),nl.
```
![alt helloworld](https://github.com/tamlt2704/tamlt2704.github.io/blob/master/pages/assets/proglog/2_hello_world.JPG "Hello world")

**nl** stands for 'start a new line'

Exit prolog
```prolog
?-halt.
```
![alt halt](https://github.com/tamlt2704/tamlt2704.github.io/blob/master/pages/assets/proglog/3_halt.JPG "Halt")

System statistics
```prolog
?-statistics.
```
![alt statistics](https://github.com/tamlt2704/tamlt2704.github.io/blob/master/pages/assets/proglog/4_statistics.JPG "statistics")

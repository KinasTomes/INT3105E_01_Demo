```
[Author] <---(n:m)---> [Book] ---(1:n)---> [BookCopy] ---(1:n)---> [Loan] <---(n:1)--- [Reader]
       \                                   ^
        \                                 /
         ------(n:1)---- [Category]     (n:1)
                                  \   /
                                  [Staff]
```
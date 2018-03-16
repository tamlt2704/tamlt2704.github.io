# simple photo editing with linux commands


**1. Resize image**

Original photo:

![Origin photo](../images/search-icon.png)

**code** 
```shell
    **convert** *search-icon.png* -resize 50x50 *search-icon-50x50.png*
    or
    **convert** -resize 50% *search-icon.png* *search-icon-50.png*
```

Result:
![resize photo](../images/search-icon-50x50.png)

**2. Combine photos**

> convert search-icon.png search-icon-50x50.png +append combined-photo.png

use **-append** for **top-to-bottom** combination
use **+append** for **left-to-right** combination

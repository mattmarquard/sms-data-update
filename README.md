# sms-data-update

This repo defines a protocol for using SMS in order to send data updates to a remote server and database. SMS is an alternative communication which can be used when mobile data is unavailable.

## Protocol:
```
SMS Body {
	Our Protocol Headers 
	{
  	2-digit SEQ #:
  	2-digit SEQ TOTAL:
  	32-digit HASH on final SEQ:
  }
  Our Protocol Body:
  { 
   	create : [{modeltype, all fields etc}, {etc}],
    action : [{model},{etc}],
    action : [{model}, {etc}]
  } 
}
```

This is currently a work in progress.

### TODO:

1. Ensure it is simple to add additional database actions other than create, update, delete.
2. Shrink the messages even further by introducing a mapping of model names to numbers:
  * one solution is to create a configuration file that can be used by the mobile application and server in order to define this mapping incorporate our code into and actual EdenMobile instances and have it interact with an actual Sahana instance
  * 
  
The MIT License (MIT)

Copyright (c) 2015 Scott Buchanan & Matthew MacLennan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

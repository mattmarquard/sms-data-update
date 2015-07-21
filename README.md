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

## auto-snapshot
[![Build Status](https://api.travis-ci.org/InnovativeTravel/auto-snapshot.svg)](https://travis-ci.org/InnovativeTravel/auto-snapshot/)

### Create snapshots for selected EBS volumes in AWS

Any volume that implement the tags bellow its snapshot will be taken:
```
tag key                             tag value
-----------------------------------------------------------------------------------
*Name                               <volume friendly name>
*auto:snapshots                     <any value>
auto:snapshot:topic                 <topic name for SNS event>
auto:snapshots:retention_days       <number of days to keep the snapshot>
```
*mandatory tags

### Example tags:

```
tag key                             tag value
-----------------------------------------------------------------------------------
Name                                my-super-important-volume
auto:snapshots                      yes
auto:snapshot:topic                 snapshot-was-created-for-my-super-important-volume
auto:snapshots:retention_days       15
```

### Usage:
Assuming aws cli is installed and set with the appropriate credentials

1. clone the repo:
```git clone https://github.com/InnovativeTravel/auto-snapshot```
2. cd into the project folder:
```cd auto-snapshot```
3. deploy to aws lambda service:
```make deploy```

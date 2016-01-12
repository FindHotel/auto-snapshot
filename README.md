# auto-snapshot

Creating snapshots for selected EBS volumes in AWS

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
1. cd into the project folder:
```cd auto-snapshot```
2. zip all python files
```zip auto-snapshot.zip *.py```
3. upload the zip file to aws Lambda service


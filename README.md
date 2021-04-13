# py2hcl
converts python objects to HCL for use in Terraform for testing, USE AT OWN RISK.

this uses a brute force approach to converting python objects into HCL... 
```
pcl = py2hcl()
dd = {'sb_permissions': {'dynamodbs': [{'arn': 'dddddddd', 'streamspec': {'StreamEnabled': True, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'write_capacity': 1}], 'eid': '///Ro9'}}
dy = pcl.dumps(dd)   
```

above will output HCL:
```
sb_permissions={
        dynamodbs = [
            {arn = "dddddddd" },
            {streamspec = {
                StreamEnabled = true
                StreamViewType = "NEW_AND_OLD_IMAGES"
             }},
            {write_capacity = 1 }
         ]
        eid = "///Ro9"
}
```

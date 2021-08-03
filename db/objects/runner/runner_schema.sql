SELECT reclada_object.create_subclass('{
    "class": "Job",
    "attrs": {
        "newClass": "Runner",
        "properties": {
            "environment": {
                "type": "string",
                "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
            },
            "status": {
                "type": "string",
                "enum ": [
                    "up",
                    "down",
                    "idle"                  
                ]
            }
        },
        "required": ["environment", "status"]
    }
}'::jsonb);

/* Just for demo */
SELECT reclada_object.create('
   {
   "class": "Runner",
    "attrs": {
        "task": "512a3dde-23c7-4771-b180-20f8781ac084",
        "type": "K8S",
        "status": "down",
        "command": "",
        "environment": "7b196912-d973-40a9-b0e2-15ecbd921b2f"
        }
     }'::jsonb);

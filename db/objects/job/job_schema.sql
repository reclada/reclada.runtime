SELECT reclada_object.create_subclass('{
    "class": "Task",
    "attrs": {
        "newClass": "Job",
        "properties": {
            "task": {
                "type": "string",
                "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
            },
            "runner": {
                "type": "string",
                "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
            },
            "status": {
                "type": "string",
                "enum ": [
                    "new",
                    "pending",
                    "running",
                    "failed",
                    "success"
                ]
            },
            "inputParameters": {
              "type": "array",
              "items": "object"
            },
            "outputParameters": {
              "type": "array",
              "items": "object"
            }
        },
        "required": ["task", "status"]
    }
}'::jsonb);
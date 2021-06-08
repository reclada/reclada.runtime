SELECT reclada_object.create_subclass('{
    "class": "Task",
    "attrs": {
        "newClass": "Pipeline",
        "properties": {
            "triggers": {
                "type": "array",
                "items": {
                    "type": "string",
                    "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
                }
            }
        },
        "required": ["triggers"]
    }
}'::jsonb);
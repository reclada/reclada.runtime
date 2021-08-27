SELECT reclada_object.create_subclass('{
    "class": "Task",
    "attrs": {
        "newClass": "Connector",
        "properties": {
            "connectionDetails": {"type": "string"},
            "name": {"type": "string"},
            "environment": {
                "type": "string",
                "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
            }
        },
        "required": ["type", "name", "environment"]
    }
}'::jsonb);

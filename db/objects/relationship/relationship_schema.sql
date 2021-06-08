SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attrs": {
        "newClass": "Relationship",
        "properties": {
            "subject": { "type": "string" },
            "object": { "type": "string" },
            "type": {
                "type": "string",
                "enum ": [
                    "params"
                ]
            }
        },
        "required": ["subject", "object", "type"]
    }
}'::jsonb);
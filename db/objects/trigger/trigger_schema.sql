SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attributes": {
        "newClass": "Trigger",
        "properties": {
            "previousJobCode": {"type": "integer"},
            "nextTask" : {
                "type": "string",
                "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
            },
            "paramsRelationships": {
                "type": "array",
                "items": {
                    "type": "string",
                    "pattern": "[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}"
                }
            }
        },
        "required": ["previousJobCode", "nextTask"]
    }
}'::jsonb);
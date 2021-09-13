SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attributes": {
        "newClass": "Environment",
        "properties": {
            "name": { "type": "string" },
            "description": { "type": "string" }
        },
        "required": ["name"]
    }
}'::jsonb);
SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attrs": {
        "newClass": "Value",
        "properties": {
            "name": { "type": "string" },
            "value": { "type": "string" }
        },
        "required": ["name"]
    }
}'::jsonb);
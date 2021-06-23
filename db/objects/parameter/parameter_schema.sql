SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attrs": {
        "newClass": "Parameter",
        "properties": {
            "name": {"type": "string"},
            "type": {
                "type": "string",
                "enum": ["code", "stdout", "stderr", "file"]
            },
            "file": {"type": "string"}
        },
        "required": ["name", "type"]
    }
}'::jsonb);
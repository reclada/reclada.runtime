SELECT reclada_object.create_subclass('{
    "class": "RecladaObject",
    "attributes": {
        "newClass": "FileExtension",
        "properties": {
            "extension": {"type": "string"},
            "mimeType": {"type": "string"}
        },
        "required": ["extension", "mimeType"]
    }
}'::jsonb);

SELECT reclada_object.create('{
    "class" : "FileExtension",
    "attributes": {
        "extension" : ".xlsx",
        "mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    }
}'::jsonb);

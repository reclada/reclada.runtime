DO LANGUAGE PLpgSQL $block$
BEGIN
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Job", "event": "create"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "job_created", "class": "Job", "event": "create", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Job", "event": "update"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "job_updated", "class": "Job", "event": "update", "attrs": ["status", "type"]}}'::jsonb);
    END IF;
    IF reclada_object.list('{"class": "Message", "attributes": {"class": "Job", "event": "delete"}}') is null THEN
        PERFORM reclada_object.create('{"class": "Message", "attributes": {"channelName": "job_deleted", "class": "Job", "event": "delete", "attrs": ["type"]}}'::jsonb);
    END IF;
END;
$block$;

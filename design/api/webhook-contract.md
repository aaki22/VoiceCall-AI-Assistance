# Webhook Contract

## `POST /inbound`

Starts a call session, generates greeting audio, plays the greeting, and asks the telephony provider to record the caller.

Response type: `application/xml`

Expected XML behavior:

```xml
<Response>
  <Play>public audio URL</Play>
  <Record action="public process-recording URL" method="POST" maxLength="10" playBeep="true"/>
</Response>
```

## `POST /process-recording`

Receives a `RecordUrl` form field, processes one call turn, plays the assistant response, and either records another turn or hangs up.

Response type: `application/xml`

Continue-call behavior:

```xml
<Response>
  <Play>thinking music URL</Play>
  <Play>assistant audio URL</Play>
  <Record action="public process-recording URL" method="POST" maxLength="10" playBeep="true"/>
</Response>
```

End-call behavior:

```xml
<Response>
  <Play>assistant audio URL</Play>
  <Hangup/>
</Response>
```

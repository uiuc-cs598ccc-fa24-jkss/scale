{{/*
    Generate a fully qualified name.
    */}}
    {{- define "fullname" -}}
    {{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
    {{- end -}}
    
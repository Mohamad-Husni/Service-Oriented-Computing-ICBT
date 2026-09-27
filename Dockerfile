FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
ARG SERVICE
WORKDIR /source
COPY Directory.Build.props ./
COPY src ./src
RUN dotnet publish src/Water.${SERVICE}/Water.${SERVICE}.csproj -c Release -o /app
FROM mcr.microsoft.com/dotnet/aspnet:10.0
ARG SERVICE
ENV SERVICE_NAME=Water.${SERVICE}.dll
WORKDIR /app
COPY --from=build /app ./
ENV ASPNETCORE_HTTP_PORTS=8080
RUN mkdir -p /app/data && chown app:app /app/data
USER app
ENTRYPOINT ["sh", "-c", "exec dotnet \"$SERVICE_NAME\""]

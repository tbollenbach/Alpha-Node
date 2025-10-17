# Update Server Example

This directory contains files for testing the update system locally.

## Files

- `test_server.py` - Simple HTTP server for testing
- `create_update_package.py` - Script to create update packages
- `updates.json` - Update manifest for version 1.0.1
- `updates_1.0.2.json` - Update manifest for version 1.0.2

## Quick Start

### 1. Create Update Packages

```bash
python create_update_package.py
```

This will:
- Create `updates/1.0.1.zip` and `updates/1.0.2.zip`
- Calculate SHA256 checksums
- Update JSON manifests with correct checksums

### 2. Start Test Server

```bash
python test_server.py
```

Server will run at `http://localhost:8000`

### 3. Test with Agent

In the main directory:

```bash
# Update config.json to point to local server
# "update_server": "http://localhost:8000/updates.json"

# Check for updates
python main.py check
```

## Deployment

For production deployment:

1. **Static Hosting**: Upload `updates.json` and packages to any web server
2. **CDN**: Use CloudFlare, AWS CloudFront, etc. for global distribution
3. **API Gateway**: Create a dynamic endpoint that generates `updates.json`
4. **S3/Azure/GCS**: Use cloud storage with HTTPS

### Example Nginx Configuration

```nginx
server {
    listen 443 ssl;
    server_name updates.example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        root /var/www/updates;
        add_header Access-Control-Allow-Origin *;
    }
}
```

### Example with AWS S3

```bash
# Upload files to S3
aws s3 cp updates.json s3://your-bucket/updates.json --acl public-read
aws s3 cp updates/ s3://your-bucket/updates/ --recursive --acl public-read

# Enable HTTPS
aws s3api put-bucket-policy --bucket your-bucket --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::your-bucket/*"
  }]
}'
```

## Security Considerations

1. **Always use HTTPS** in production
2. **Verify checksums** are calculated correctly
3. **Sign packages** with GPG for additional security
4. **Rate limit** your update endpoint to prevent abuse
5. **Monitor** access logs for suspicious activity

## Creating New Updates

1. Make changes to modules or core files
2. Update version number
3. Run `create_update_package.py` (modify for new version)
4. Test locally before deploying
5. Deploy to production server


# How to
Copy the file "secrets.env.template" to "secretes.env" and set the variables in the file.

Make sure you have the right certificates in your dockerimage. 
On docker build, there has to be a cert-bundle containing ??? on the build-root.

Then run docker-compose up -d

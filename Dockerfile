# Create a slim final image
FROM mysql:8.0 AS builder

WORKDIR /app

# Set environment variables (optional)
ENV MYSQL_ROOT_PASSWORD=root_pass
ENV MYSQL_DATABASE=pseudo_database

# Initialize the database
COPY init_db.sql /docker-entrypoint-initdb.d/

# Expose the MySQL port
EXPOSE 3306

# Command to run MySQL
CMD ["mysqld"]

HEALTHCHECK --interval=2s CMD ["mysqladmin", "ping"]


# Use a multi-stage build for efficiency
FROM python:3.8 AS production

# Set working directory
WORKDIR /app

COPY --from=builder /app/var/lib/mysql /var/lib/mysql

# Install dependencies
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Expose the MySQL port
EXPOSE 8501

HEALTHCHECK --interval=2s CMD ["mysqladmin", "ping"]

# Define Streamlit entrypoint
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
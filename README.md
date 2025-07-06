# Hotel Booking System - Microservices Application

This is a comprehensive hotel booking system built with microservices architecture for DevOps deployment demonstration.

## Architecture Overview

### 🏗️ Microservices
- **Hotel Service** (Port 5001): Manages hotel listings, room types, and amenities
- **Booking Service** (Port 5002): Handles room availability, check-in/check-out, and booking records
- **User Service** (Port 5003): Manages user authentication and profiles
- **Review Service** (Port 5004): Collects ratings and reviews from customers
- **Payment Service** (Port 5005): Handles invoicing, booking confirmations, and fake payment gateway

### 🎯 Frontend
- **Hotel Frontend** (Port 80): Simple HTML/CSS/JavaScript interface
- Real-time navigation with URL updates
- Responsive design for all devices
- Admin panel for hotel management

### 🗄️ Database
- **MySQL 8.0**: Centralized database for all services
- Docker container with persistent volume
- Sample data initialization

## 🚀 Deployment Options

### 1. Local Docker Compose Deployment

```bash
# Clone the repository
git clone https://github.com/your-repo/hotel-booking-system.git
cd hotel-booking-system

# Deploy with Docker Compose
docker-compose up -d

# Access the application
# Frontend: http://your-ec2-public-ip
# Services: http://your-ec2-public-ip:5001-5005
```

### 2. Jenkins CI/CD Pipeline

Each service has its own Jenkins pipeline with build parameters:

#### Pipeline Features:
- **Build with Parameters**: Environment selection (dev/staging/prod)
- **Docker Build**: Automated Docker image creation
- **DockerHub Push**: Automatic image publishing
- **Kubernetes Deploy**: Optional K8s deployment with parameter

#### Setup Jenkins Jobs:
1. Create separate pipeline jobs for each service
2. Configure GitHub webhook for automatic builds
3. Set up the following credentials:
   - `dockerhub-creds`: DockerHub username/password
   - `aws-creds`: AWS Access Key/Secret Key

#### Run Pipeline:
```bash
# Build and deploy specific service
# Use "Build with Parameters" option in Jenkins
# Select environment and enable K8s deployment
```

### 3. AWS EKS Kubernetes Deployment

#### Prerequisites:
```bash
# Install AWS CLI and kubectl
aws configure
aws eks update-kubeconfig --region us-east-1 --name kastro-eks
```

#### Deploy Database:
```bash
kubectl apply -f k8s/mysql-deployment.yaml
```

#### Deploy Services:
```bash
# Deploy all services
kubectl apply -f hotel-service/k8s/
kubectl apply -f booking-service/k8s/
kubectl apply -f user-service/k8s/
kubectl apply -f review-service/k8s/
kubectl apply -f payment-service/k8s/
kubectl apply -f frontend/k8s/
```

#### Access Services:
```bash
# Get service URLs
kubectl get services
kubectl get pods

# Access frontend via NodePort
http://your-worker-node-ip:30080
```

### 4. Ingress Controller Deployment

#### Install Ingress Controller:
```bash
kubectl apply -f k8s/ingress-controller.yaml
```

#### Deploy Ingress Rules:
```bash
kubectl apply -f k8s/ingress.yaml
```

#### Update Local DNS:
```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
your-load-balancer-ip hotel-booking.local
```

#### Access Application:
```bash
# Via Ingress
http://hotel-booking.local
```

## 🔧 Database Access

### Docker Compose:
```bash
# Connect to MySQL container
docker exec -it hotel-booking-system_mysql-db_1 mysql -u root -ppassword

# Use the database
USE hotel_booking;
SHOW TABLES;
```

### Kubernetes:
```bash
# Get MySQL pod name
kubectl get pods | grep mysql

# Connect to MySQL pod
kubectl exec -it mysql-deployment-xxxxx-xxxxx -- mysql -u root -ppassword

# Use the database
USE hotel_booking;
SHOW TABLES;
```

## 📊 Application Features

### User Features:
- **Simple Login**: Any email address for quick access
- **Hotel Browsing**: View available hotels with details
- **Room Booking**: Select dates and book rooms
- **Payment Processing**: Fake payment gateway simulation
- **Review System**: Rate and review hotels
- **Booking History**: View past bookings

### Admin Features:
- **Hotel Management**: Add/remove hotels
- **Dashboard**: View statistics and analytics
- **User Management**: View all users
- **Booking Management**: View all bookings
- **Review Management**: View all reviews

## 🛠️ Development

### Service Ports:
- Frontend: 80
- Hotel Service: 5001
- Booking Service: 5002
- User Service: 5003
- Review Service: 5004
- Payment Service: 5005
- MySQL: 3306

### Default Credentials:
- **Admin User**: admin@hotel.com / admin123
- **Database**: root / password

### Health Check Endpoints:
- `/health` - Available on all services (5001-5005)

## 🔍 Monitoring & Logs

### Docker Compose:
```bash
# View logs
docker-compose logs -f [service-name]

# View all services
docker-compose ps
```

### Kubernetes:
```bash
# View pod logs
kubectl logs -f deployment/hotel-service

# View all deployments
kubectl get deployments

# View services
kubectl get services
```

## 🧪 Testing

### API Testing:
```bash
# Test hotel service
curl http://your-ip:5001/hotels

# Test user service
curl http://your-ip:5003/users

# Test health endpoints
curl http://your-ip:5001/health
```

### Frontend Testing:
1. Open browser: `http://your-ec2-public-ip`
2. Login with any email
3. Browse hotels and make bookings
4. Write reviews
5. Access admin panel (admin@hotel.com)

## 📝 CI/CD Pipeline Process

### Level 1: Jenkins CI/CD
1. **Code Commit**: Push to GitHub
2. **Jenkins Trigger**: Webhook triggers build
3. **Docker Build**: Create service images
4. **Push to Registry**: Upload to DockerHub
5. **K8s Deploy**: Deploy to EKS cluster

### Level 2: Ingress Controller
1. **Install Controller**: Deploy NGINX ingress
2. **Configure Rules**: Set up routing
3. **DNS Configuration**: Update hosts file
4. **Load Balancer**: Access via domain

## 🚨 Troubleshooting

### Common Issues:

1. **Database Connection Failed**:
   ```bash
   # Check MySQL container
   docker logs hotel-booking-system_mysql-db_1
   
   # In K8s
   kubectl logs deployment/mysql-deployment
   ```

2. **Service Not Accessible**:
   ```bash
   # Check service status
   kubectl get pods
   kubectl describe pod [pod-name]
   ```

3. **Ingress Issues**:
   ```bash
   # Check ingress controller
   kubectl get pods -n ingress-nginx
   kubectl logs -n ingress-nginx deployment/nginx-ingress-controller
   ```

## 📋 Deployment Checklist

### Before Deployment:
- [ ] AWS EKS cluster running (kastro-eks)
- [ ] Jenkins configured with credentials
- [ ] DockerHub account accessible
- [ ] kubectl configured for EKS
- [ ] EC2 security groups allow required ports

### Docker Compose Deployment:
- [ ] Clone repository
- [ ] Run `docker-compose up -d`
- [ ] Access via EC2 public IP
- [ ] Test all services

### Jenkins CI/CD:
- [ ] Create pipeline jobs for each service
- [ ] Test build with parameters
- [ ] Deploy to K8s cluster
- [ ] Verify deployments

### Ingress Setup:
- [ ] Deploy ingress controller
- [ ] Configure ingress rules
- [ ] Update DNS/hosts file
- [ ] Test domain access

## 🎉 Success Criteria

✅ **Application Accessible**: Frontend loads successfully  
✅ **User Authentication**: Login works with any email  
✅ **Hotel Browsing**: Hotels display with details  
✅ **Booking Flow**: Complete booking process works  
✅ **Payment Processing**: Fake payment gateway responds  
✅ **Review System**: Users can write and view reviews  
✅ **Admin Functions**: Admin can add/remove hotels  
✅ **Database Persistence**: Data survives container restarts  
✅ **CI/CD Pipeline**: Jenkins builds and deploys successfully  
✅ **Ingress Access**: Domain-based access works  

## 📞 Support

For deployment issues or questions:
1. Check logs first (`docker-compose logs` or `kubectl logs`)
2. Verify network connectivity
3. Check security groups and firewall rules
4. Ensure all services are running

---

**Note**: This application is designed for educational DevOps purposes. All payment processing is simulated and not connected to real payment gateways.
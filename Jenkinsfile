pipeline {
    agent any
    
    parameters {
        choice(
            name: 'SERVICE',
            choices: ['all', 'hotel-service', 'booking-service', 'user-service', 'review-service', 'payment-service', 'frontend'],
            description: 'Select service to deploy'
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Select deployment environment'
        )
        booleanParam(
            name: 'DEPLOY_TO_K8S',
            defaultValue: false,
            description: 'Deploy to Kubernetes cluster'
        )
    }
    
    environment {
        DOCKER_TAG = "${BUILD_NUMBER}"
        AWS_REGION = "us-east-1"
        EKS_CLUSTER = "kastro-eks"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build and Push Services') {
            parallel {
                stage('Hotel Service') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'hotel-service'
                        }
                    }
                    steps {
                        script {
                            dir('hotel-service') {
                                def image = docker.build("kastrov/hotel-service:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
                
                stage('Booking Service') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'booking-service'
                        }
                    }
                    steps {
                        script {
                            dir('booking-service') {
                                def image = docker.build("kastrov/booking-service:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
                
                stage('User Service') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'user-service'
                        }
                    }
                    steps {
                        script {
                            dir('user-service') {
                                def image = docker.build("kastrov/user-service:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
                
                stage('Review Service') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'review-service'
                        }
                    }
                    steps {
                        script {
                            dir('review-service') {
                                def image = docker.build("kastrov/review-service:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
                
                stage('Payment Service') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'payment-service'
                        }
                    }
                    steps {
                        script {
                            dir('payment-service') {
                                def image = docker.build("kastrov/payment-service:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
                
                stage('Frontend') {
                    when {
                        anyOf {
                            params.SERVICE == 'all'
                            params.SERVICE == 'frontend'
                        }
                    }
                    steps {
                        script {
                            dir('frontend') {
                                def image = docker.build("kastrov/hotel-frontend:${DOCKER_TAG}")
                                docker.withRegistry('https://registry.hub.docker.com', 'dockerhub-creds') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                params.DEPLOY_TO_K8S == true
            }
            steps {
                script {
                    withCredentials([aws(accessKeyVariable: 'AWS_ACCESS_KEY_ID', 
                                       credentialsId: 'aws-creds', 
                                       secretKeyVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                        sh """
                            aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}
                            
                            # Deploy MySQL first
                            kubectl apply -f k8s/mysql-deployment.yaml
                            
                            # Wait for MySQL to be ready
                            kubectl wait --for=condition=ready pod -l app=mysql --timeout=300s
                            
                            # Deploy services based on selection
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "hotel-service" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' hotel-service/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f hotel-service/k8s/service.yaml
                            fi
                            
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "booking-service" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' booking-service/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f booking-service/k8s/service.yaml
                            fi
                            
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "user-service" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' user-service/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f user-service/k8s/service.yaml
                            fi
                            
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "review-service" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' review-service/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f review-service/k8s/service.yaml
                            fi
                            
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "payment-service" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' payment-service/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f payment-service/k8s/service.yaml
                            fi
                            
                            if [ "${params.SERVICE}" = "all" ] || [ "${params.SERVICE}" = "frontend" ]; then
                                sed 's|IMAGE_TAG|${DOCKER_TAG}|g\' frontend/k8s/deployment.yaml | kubectl apply -f -
                                kubectl apply -f frontend/k8s/service.yaml
                            fi
                            
                            # Show deployment status
                            kubectl get deployments
                            kubectl get services
                            kubectl get pods
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh 'docker system prune -f'
        }
        success {
            echo "Deployment completed successfully!"
        }
        failure {
            echo "Deployment failed. Check logs for details."
        }
    }
}
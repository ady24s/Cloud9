import axios from 'axios';

export const fetchAWSInstances = async () => {
  const response = await axios.get('http://127.0.0.1:8000/aws/instances');
  return response.data;
};

export const fetchS3Buckets = async () => {
  const response = await axios.get('http://127.0.0.1:8000/aws/s3');
  return response.data;
};

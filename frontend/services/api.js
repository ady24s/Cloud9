import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000"; // Your backend's base URL

// Fetch all resources
export const fetchResources = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/resources/`);
        return response.data;
    } catch (error) {
        console.error("Error fetching resources:", error);
        return [];
    }
};

// Fetch AWS instances
export const fetchAWSInstances = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/aws/instances`);
        return response.data.instances;
    } catch (error) {
        console.error("Error fetching AWS instances:", error);
        return [];
    }
};
export const fetchS3Buckets = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/aws/s3`);
        return response.data.buckets;
    } catch (error) {
        console.error("Error fetching S3 buckets:", error);
        return [];
    }
};

export const fetchIdleInstances = async () => {
    try {
        const response = await axios.get(`${BASE_URL}/aws/idle-instances`);
        return response.data.idle_instances;
    } catch (error) {
        console.error("Error fetching idle instances:", error);
        return [] ;
    }
};

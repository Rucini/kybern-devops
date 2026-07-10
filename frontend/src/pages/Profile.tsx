import { useEffect, useState } from 'react';
import { Card, Descriptions, Typography, Spin, message } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import api from '../api/axios';


const { Title } = Typography;

const Profile = () => {
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/auth/me');
      setProfileData(response.data);
    } catch (error) {
      message.error('Failed to load profile data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Spin size="large" style={{ display: 'flex', justifyContent: 'center', marginTop: 50 }} />;
  }

  if (!profileData) {
    return <div>Profile not found.</div>;
  }

  return (
    <Card 
      title={<Title level={3} style={{ margin: 0 }}><UserOutlined /> User Profile</Title>} 
      style={{ maxWidth: 800, margin: '0 auto', marginTop: 24 }}
    >
      <Descriptions bordered column={1}>
        <Descriptions.Item label="User ID">{profileData.id}</Descriptions.Item>
        <Descriptions.Item label="Username">{profileData.username}</Descriptions.Item>
        <Descriptions.Item label="Email">{profileData.email}</Descriptions.Item>
        <Descriptions.Item label="Role">
          <span style={{ textTransform: 'capitalize' }}>{profileData.role}</span>
        </Descriptions.Item>
        <Descriptions.Item label="Account Created">
          {profileData.created_at ? new Date(profileData.created_at).toLocaleString() : 'N/A'}
        </Descriptions.Item>
      </Descriptions>
    </Card>
  );
};

export default Profile;

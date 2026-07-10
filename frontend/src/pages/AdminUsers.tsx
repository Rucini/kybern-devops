import { useEffect, useState } from 'react';
import { Table, Button, Typography, Space, message, Modal, Tag } from 'antd';
import api from '../api/axios';

const { Title } = Typography;

const AdminUsers = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 15, total: 0 });

  useEffect(() => {
    fetchUsers();
  }, [pagination.current]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/admin/users?page=${pagination.current}`);
      setData(response.data.items);
      setPagination({ ...pagination, total: response.data.total });
    } catch (error) {
      message.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination: any) => {
    setPagination(newPagination);
  };

  const handleResetPassword = (userId: number, username: string) => {
    Modal.confirm({
      title: `Reset Password for ${username}?`,
      content: 'This will reset their password to the default "password123". Are you sure?',
      okText: 'Yes, Reset',
      okType: 'danger',
      cancelText: 'Cancel',
      onOk: async () => {
        try {
          await api.post(`/admin/users/${userId}/reset_password`);
          message.success(`Password reset for ${username}`);
        } catch (error) {
          message.error('Failed to reset password');
        }
      },
    });
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Username',
      dataIndex: 'username',
      key: 'username',
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role: string) => {
        return <Tag color={role === 'admin' ? 'purple' : 'blue'}>{role.toUpperCase()}</Tag>;
      }
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button 
            type="link" 
            danger 
            onClick={() => handleResetPassword(record.id, record.username)} 
            style={{ padding: 0 }}
          >
            Reset Password
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>Admin - All Users</Title>
      </div>
      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
      />
    </div>
  );
};

export default AdminUsers;

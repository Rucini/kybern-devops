import { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Table, Typography, Tag } from 'antd';
import { CheckCircleOutlined, SyncOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../contexts/AuthContext';

const { Title } = Typography;

const Dashboard = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await api.get('/main/dashboard');
      setData(response.data);
    } catch (error) {
      console.error("Failed to fetch dashboard", error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
    },
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      render: (text: string, record: any) => <Link to={`/tickets/${record.id}`}>{text}</Link>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        let color = status === 'Closed' || status === 'Resolved' ? 'green' : 'geekblue';
        return <Tag color={color}>{status.toUpperCase()}</Tag>;
      },
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
  ];

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Open Tickets"
              value={data?.open_tickets || 0}
              valueStyle={{ color: '#cf1322' }}
              prefix={<FolderOpenOutlined />}
            />
          </Card>
        </Col>
        {user?.role === 'admin' && (
          <Col span={8}>
            <Card>
              <Statistic
                title="In Progress"
                value={data?.in_progress_tickets || 0}
                valueStyle={{ color: '#d48806' }}
                prefix={<SyncOutlined spin />}
              />
            </Card>
          </Col>
        )}
        <Col span={8}>
          <Card>
            <Statistic
              title="Resolved/Closed Tickets"
              value={data?.resolved_tickets || 0}
              valueStyle={{ color: '#3f8600' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Recent Tickets">
        <Table 
          columns={columns} 
          dataSource={data?.recent_tickets || []} 
          rowKey="id" 
          pagination={false}
          loading={loading}
        />
      </Card>
    </div>
  );
};

export default Dashboard;

import { useEffect, useState } from 'react';
import { Table, Button, Typography, Tag, Space, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';

const { Title } = Typography;

const TicketList = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10, total: 0 });
  const navigate = useNavigate();

  useEffect(() => {
    fetchTickets();
  }, [pagination.current]);

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/tickets/?page=${pagination.current}`);
      setData(response.data.items);
      setPagination({ ...pagination, total: response.data.total });
    } catch (error) {
      message.error("Failed to load tickets");
    } finally {
      setLoading(false);
    }
  };

  const handleTableChange = (newPagination: any) => {
    setPagination(newPagination);
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
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
    },
    {
      title: 'Type',
      key: 'type',
      render: (_: any, record: any) => {
        // If the ticket's author matches the assigned_to, or if we just want to know if they own it:
        // Actually, we can just check if they are the creator or assignee based on local user ID, 
        // but we don't have user context here directly without useAuth(). 
        // Let's just show Assigned To:
        return record.assignee_name ? <Tag color="purple">{record.assignee_name}</Tag> : <Tag>Unassigned</Tag>;
      },
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
          <Link to={`/tickets/${record.id}`}>View</Link>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>My Tickets</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/tickets/create')}>
          Create Ticket
        </Button>
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

export default TicketList;

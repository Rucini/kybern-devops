import { useEffect, useState } from 'react';
import { Table, Button, Typography, Space, message, Select, Modal } from 'antd';
import { Link } from 'react-router-dom';
import api from '../api/axios';

const { Title } = Typography;
const { Option } = Select;

const AdminTickets = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<any[]>([]);
  const [pagination, setPagination] = useState({ current: 1, pageSize: 15, total: 0 });

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    fetchTickets();
  }, [pagination.current]);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users?per_page=1000');
      setUsers(response.data.items);
    } catch (error) {
      console.error("Failed to load users for assignment dropdown");
    }
  };

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/admin/tickets?page=${pagination.current}`);
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

  const handleStatusChange = async (ticketId: number, newStatus: string) => {
    try {
      await api.put(`/admin/tickets/${ticketId}/status`, { status: newStatus });
      message.success('Status updated');
      fetchTickets();
    } catch (error) {
      message.error('Failed to update status');
    }
  };

  const handleAssign = async (ticketId: number, assigneeId: number) => {
    try {
      await api.put(`/admin/tickets/${ticketId}/assign`, { assignee_id: assigneeId });
      message.success('Ticket assigned');
      fetchTickets();
    } catch (error) {
      message.error('Failed to assign ticket');
    }
  };

  const handleDelete = (ticketId: number) => {
    Modal.confirm({
      title: 'Are you sure you want to delete this ticket?',
      content: 'This action cannot be undone.',
      okText: 'Yes',
      okType: 'danger',
      cancelText: 'No',
      onOk: async () => {
        try {
          await api.delete(`/admin/tickets/${ticketId}`);
          message.success('Ticket deleted');
          fetchTickets();
        } catch (error) {
          message.error('Failed to delete ticket');
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
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
    },
    {
      title: 'Status',
      key: 'status',
      render: (_: any, record: any) => {
        return (
          <Select 
            value={record.status} 
            style={{ width: 120 }} 
            onChange={(val) => handleStatusChange(record.id, val)}
          >
            <Option value="Open">Open</Option>
            <Option value="Assigned">Assigned</Option>
            <Option value="In Progress">In Progress</Option>
            <Option value="Resolved">Resolved</Option>
            <Option value="Closed">Closed</Option>
          </Select>
        );
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
      title: 'Assigned To',
      key: 'assigned_to',
      render: (_: any, record: any) => {
        return (
          <Select 
            value={record.assigned_to} 
            style={{ width: 150 }} 
            onChange={(val) => handleAssign(record.id, val)}
            placeholder="Unassigned"
            allowClear
            onClear={() => handleAssign(record.id, 0)} // Optional, if backend handles clearing
          >
            {users.map(u => (
              <Option key={u.id} value={u.id}>{u.username}</Option>
            ))}
          </Select>
        );
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
          <Button type="link" danger onClick={() => handleDelete(record.id)} style={{ padding: 0 }}>
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2} style={{ margin: 0 }}>Admin - All Tickets</Title>
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

export default AdminTickets;

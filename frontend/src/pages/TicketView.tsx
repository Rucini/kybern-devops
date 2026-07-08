import { useEffect, useState } from 'react';
import { Card, Typography, Tag, Descriptions, Button, List, Input, Form, message, Space } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;
const { TextArea } = Input;

const TicketView = () => {
  const { id } = useParams<{ id: string }>();
  const [ticket, setTicket] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [commentLoading, setCommentLoading] = useState(false);
  useAuth();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  useEffect(() => {
    fetchTicket();
  }, [id]);

  const fetchTicket = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/tickets/${id}`);
      setTicket(response.data);
    } catch (error) {
      message.error("Failed to load ticket");
      navigate('/tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleAddComment = async (values: any) => {
    setCommentLoading(true);
    try {
      await api.post(`/tickets/${id}/comments`, values);
      message.success("Comment added");
      form.resetFields();
      fetchTicket();
    } catch (error) {
      message.error("Failed to add comment");
    } finally {
      setCommentLoading(false);
    }
  };

  const handleCloseTicket = async () => {
    try {
      await api.post(`/tickets/${id}/close`);
      message.success("Ticket closed");
      fetchTicket();
    } catch (error) {
      message.error("Failed to close ticket");
    }
  };

  if (loading || !ticket) return <div>Loading...</div>;

  let statusColor = ticket.status === 'Closed' || ticket.status === 'Resolved' ? 'green' : 'geekblue';

  return (
    <Space direction="vertical" size="large" style={{ display: 'flex' }}>
      <Card
        title={<Title level={3} style={{ margin: 0 }}>{ticket.title}</Title>}
        extra={<Tag color={statusColor}>{ticket.status.toUpperCase()}</Tag>}
      >
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Ticket ID">{ticket.id}</Descriptions.Item>
          <Descriptions.Item label="Category">{ticket.category}</Descriptions.Item>
          <Descriptions.Item label="Priority">{ticket.priority}</Descriptions.Item>
          <Descriptions.Item label="Created By">{ticket.author_name}</Descriptions.Item>
          <Descriptions.Item label="Assigned To">{ticket.assignee_name || 'Unassigned'}</Descriptions.Item>
          <Descriptions.Item label="Created At">{new Date(ticket.created_at).toLocaleString()}</Descriptions.Item>
        </Descriptions>
        
        <div style={{ marginTop: 24 }}>
          <Title level={5}>Description</Title>
          <div style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: 16, borderRadius: 8 }}>
            {ticket.description}
          </div>
        </div>

        {ticket.attachment && (
          <div style={{ marginTop: 24 }}>
            <Title level={5}>Attachment</Title>
            <Button 
              type="dashed" 
              href={`${import.meta.env.VITE_API_URL || '/api'}/tickets/download/${ticket.attachment}`} 
              target="_blank"
            >
              Download {ticket.attachment}
            </Button>
          </div>
        )}

        <div style={{ marginTop: 24 }}>
          {ticket.status !== 'Closed' && (
            <Button danger onClick={handleCloseTicket}>Close Ticket</Button>
          )}
        </div>
      </Card>

      <Card title="Comments">
        <List
          itemLayout="horizontal"
          dataSource={ticket.comments || []}
          renderItem={(comment: any) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <Space>
                    <Text strong>{comment.author_name}</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {new Date(comment.created_at).toLocaleString()}
                    </Text>
                  </Space>
                }
                description={<div style={{ whiteSpace: 'pre-wrap', color: 'black' }}>{comment.body}</div>}
              />
            </List.Item>
          )}
        />

        {ticket.status !== 'Closed' && (
          <Form form={form} onFinish={handleAddComment} style={{ marginTop: 24 }}>
            <Form.Item name="body" rules={[{ required: true, message: 'Please enter a comment' }]}>
              <TextArea rows={4} placeholder="Add a comment..." />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={commentLoading}>
                Post Comment
              </Button>
            </Form.Item>
          </Form>
        )}
      </Card>
    </Space>
  );
};

export default TicketView;

import { useState } from 'react';
import { Form, Input, Button, Select, Upload, message, Typography, Card } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const TicketCreate = () => {
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('title', values.title);
    formData.append('description', values.description);
    formData.append('category', values.category);
    formData.append('priority', values.priority);

    if (fileList.length > 0) {
      formData.append('attachment', fileList[0].originFileObj);
    }

    try {
      const response = await api.post('/tickets/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      message.success('Ticket created successfully!');
      navigate(`/tickets/${response.data.ticket.id}`);
    } catch (error) {
      message.error('Failed to create ticket');
    } finally {
      setLoading(false);
    }
  };

  const uploadProps = {
    onRemove: (_file: any) => {
      setFileList([]);
    },
    beforeUpload: (_file: any) => {
      setFileList([_file]);
      return false; // Prevent auto upload
    },
    fileList,
  };

  return (
    <Card>
      <Title level={2}>Create New Ticket</Title>
      <Form layout="vertical" onFinish={onFinish} initialValues={{ priority: 'Medium' }}>
        <Form.Item name="title" label="Title" rules={[{ required: true, message: 'Please enter a title' }]}>
          <Input placeholder="Ticket Title" />
        </Form.Item>
        
        <Form.Item name="category" label="Category" rules={[{ required: true, message: 'Please select a category' }]}>
          <Select placeholder="Select a category">
            <Option value="Network">Network</Option>
            <Option value="Hardware">Hardware</Option>
            <Option value="Software">Software</Option>
            <Option value="Email">Email</Option>
            <Option value="Server">Server</Option>
            <Option value="Security">Security</Option>
          </Select>
        </Form.Item>

        <Form.Item name="priority" label="Priority" rules={[{ required: true, message: 'Please select a priority' }]}>
          <Select placeholder="Select priority">
            <Option value="Low">Low</Option>
            <Option value="Medium">Medium</Option>
            <Option value="High">High</Option>
            <Option value="Critical">Critical</Option>
          </Select>
        </Form.Item>

        <Form.Item name="description" label="Description" rules={[{ required: true, message: 'Please enter a description' }]}>
          <TextArea rows={4} placeholder="Describe the issue in detail" />
        </Form.Item>

        <Form.Item label="Attachment">
          <Upload {...uploadProps} maxCount={1}>
            <Button icon={<UploadOutlined />}>Select File</Button>
          </Upload>
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading}>
            Submit Ticket
          </Button>
          <Button style={{ marginLeft: 8 }} onClick={() => navigate('/tickets')}>
            Cancel
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default TicketCreate;

import {Button, Form, Input} from 'antd'
import {FC} from 'react'
import {Link} from 'react-router-dom'

interface AuthComponentProps {
    title_text?: string
    button_text?: string
    is_password?: boolean
    link_text?: string
    link_path?: string
}

const AuthComponent: FC<AuthComponentProps> = ({
    title_text = "Sign in",
    is_password = true,
    button_text = "Login",
    link_text = "New User?",
    link_path = "/check-user"
}) => {
    return <div className='login'>
        <div className='inner'>
            <div className="header">
                <h3>{title_text}</h3>
                <h2>Inventory</h2>
            </div>
            <Form layout="vertical" >
                <Form.Item label="Username" required>
                    <Input placeholder="input username" required />
                </Form.Item>
                {is_password &&
                    <Form.Item label="Password" required>
                        <Input placeholder="input password" type='password' auto-complete="current-password" required />
                    </Form.Item>}
                <Form.Item>
                    <Button type="primary" block>{button_text}</Button>
                </Form.Item>
            </Form>
            <Link to={link_path}>{link_text}</Link>
        </div>
    </div>
}

export default AuthComponent
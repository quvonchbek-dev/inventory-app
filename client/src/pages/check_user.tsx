import {FC} from 'react'
import AuthComponent from '../components/AuthComponent'

const CheckUser: FC = () => {
    return <AuthComponent
        title_text='Verify Yourself'
        link_text='Go back'
        link_path='/login'
        button_text='Submit'
        is_password={false}
    />
}
export default CheckUser
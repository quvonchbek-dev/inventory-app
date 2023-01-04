import {BrowserRouter, Route, Routes} from 'react-router-dom'
import {FC} from 'react'
import Login from './pages/login'
import CheckUser from './pages/check_user'


const Router: FC = () => {
    return <BrowserRouter>
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/check-user" element={<CheckUser />} />
        </Routes>
    </BrowserRouter>
}

export default Router
import {BrowserRouter, Route, Switch} from 'react-router-dom'
import {FC} from 'react'

const Router: FC = () => {
    return <BrowserRouter>
        <Switch>
            <Route path="/login" exact component></Route>
        </Switch>
    </BrowserRouter>
}

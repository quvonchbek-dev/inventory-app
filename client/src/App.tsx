import {FC} from "react";

interface MyCompros {
    name: string
    age: number
}

const App: FC<MyCompros> = ({name, age}) => {
    return (
        <div><h1>
            {name} - {age}{" "}
        </h1>
        </div>
    );
};

export default App;

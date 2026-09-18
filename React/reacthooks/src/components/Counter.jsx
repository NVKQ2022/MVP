import { useEffect, useState, useRef} from "react";
import ResetConfirmation from "./ResetConfirmation";
import RenderInfo from "./RenderInfo";
import CounterControls from "./CounterControls"
import {useTheme} from "../contexts/ThemeContext"
import "./Counter.css";
function Counter() {
    const [count, setCount] = useState(0);
    const { theme } = useTheme();
    // Previous count
    const previousCount = useRef(0);

    // Render counter
    const renderCount = useRef(0);
    renderCount.current++;
    const onIncrement = () => {
        console.log("Increase count")
        setCount(count + 1)
    }
    const onDecrement = () => {
        console.log("Decrease count")
        setCount(count - 1)
    }
    const onReset = () => {
        console.log("Reset count")

        setCount(0)
    }

    useEffect(() => {
        document.title = `Count: ${count}`
        return () => {
            document.title = "React App"
        }
    }, [count])
    // Save current count for the next render  
    useEffect(() => {
        previousCount.current = count;
    }, [count]);
    return (
        <div className={`counter ${theme}`}>
          <h1>Count: {count}</h1>
          <CounterControls
              onIncrement={onIncrement}
              onDecrement={onDecrement}
              onReset={onReset }
          />
          
          
          <RenderInfo
              previousCount={previousCount.current}
              renderCount={renderCount.current}
          />
      </div>
  );
}

export default Counter;
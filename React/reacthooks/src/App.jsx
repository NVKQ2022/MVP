import './App.css'
import Counter from './components/Counter'
import { ThemeProvider } from './contexts/ThemeContext'
import ThemeToggle from './components/ThemeToggle'

function App() {
  return (
      <ThemeProvider>
          <header className="app-header">
              <ThemeToggle />
          </header>
          <main className="app-main">
              <Counter />
          </main>
      </ThemeProvider>
  )
}

export default App

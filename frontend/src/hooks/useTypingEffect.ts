import { useState, useEffect } from 'react'

export const useTypingEffect = (
  text: string,
  speed: number = 100,
  delay: number = 0
) => {
  const [displayedText, setDisplayedText] = useState('')
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    let timeout: NodeJS.Timeout
    let currentIndex = 0

    const startTyping = () => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1))
        currentIndex++
        timeout = setTimeout(startTyping, speed)
      } else {
        setIsComplete(true)
      }
    }

    timeout = setTimeout(startTyping, delay)

    return () => {
      clearTimeout(timeout)
    }
  }, [text, speed, delay])

  return { displayedText, isComplete }
}

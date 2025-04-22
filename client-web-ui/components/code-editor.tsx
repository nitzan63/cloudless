"use client"

import type React from "react"
import dynamic from "next/dynamic"
import { useState } from "react"

// Dynamically import Monaco Editor to avoid SSR issues
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="h-full flex items-center justify-center bg-muted">
      <p className="text-muted-foreground">Loading editor...</p>
    </div>
  ),
})

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  language?: string
}

export default function CodeEditor({ value, onChange, language = "python" }: CodeEditorProps) {
  return (
    <div className="h-full">
      <MonacoEditor
        height="100%"
        defaultLanguage={language}
        value={value}
        onChange={(value) => value !== undefined && onChange(value)}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: "on",
          roundedSelection: false,
          scrollBeyondLastLine: false,
          readOnly: false,
          automaticLayout: true,
          tabSize: 4,
          wordWrap: "on",
          lineHeight: 1.5,
          padding: { top: 16, bottom: 16 },
        }}
      />
    </div>
  )
}

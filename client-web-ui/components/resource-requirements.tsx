"use client"

import { useState } from "react"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Info } from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface ResourceRequirementsProps {
  onSpecsChange: (specs: { cpuCores: number; memoryGB: number; storageGB: number }) => void
}

const PRESET_CONFIGS = {
  light: {
    name: "Light Task",
    description: "Small datasets, simple models (e.g., linear regression, small neural networks)",
    specs: { cpuCores: 2, memoryGB: 4, storageGB: 10 },
  },
  medium: {
    name: "Medium Task",
    description: "Medium datasets, moderate models (e.g., random forests, medium neural networks)",
    specs: { cpuCores: 4, memoryGB: 8, storageGB: 20 },
  },
  heavy: {
    name: "Heavy Task",
    description: "Large datasets, complex models (e.g., deep learning, large-scale training)",
    specs: { cpuCores: 8, memoryGB: 16, storageGB: 50 },
  },
}

export default function ResourceRequirements({ onSpecsChange }: ResourceRequirementsProps) {
  const [selectedPreset, setSelectedPreset] = useState<keyof typeof PRESET_CONFIGS>("medium")

  const handlePresetChange = (value: string) => {
    const preset = value as keyof typeof PRESET_CONFIGS
    setSelectedPreset(preset)
    onSpecsChange(PRESET_CONFIGS[preset].specs)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Resource Requirements
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>Choose a preset configuration based on your task requirements</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <RadioGroup
          value={selectedPreset}
          onValueChange={handlePresetChange}
          className="grid gap-4"
        >
          {Object.entries(PRESET_CONFIGS).map(([key, config]) => (
            <div key={key} className="flex items-center space-x-2">
              <RadioGroupItem value={key} id={key} />
              <Label htmlFor={key} className="flex flex-col">
                <span className="font-medium">{config.name}</span>
                <span className="text-sm text-muted-foreground">
                  {config.description}
                </span>
                <span className="text-xs text-muted-foreground mt-1">
                  {config.specs.cpuCores} CPU cores • {config.specs.memoryGB}GB RAM • {config.specs.storageGB}GB storage
                </span>
              </Label>
            </div>
          ))}
        </RadioGroup>
      </CardContent>
    </Card>
  )
} 
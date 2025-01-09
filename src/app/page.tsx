
'use client'
import { Button, Slider} from "@nextui-org/react";

export default function Home() {
  return (
    <div>
      <Button> Click me </Button>
      <Slider className="max-w-md"
      defaultValue={0.4}
      label="temperature"
      maxValue={1}
      minValue={0}
      step={0.01}
      />
    </div>
  );
}

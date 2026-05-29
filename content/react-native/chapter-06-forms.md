# Chapter 6: Forms & Input

[prev: Working with APIs](./chapter-05-apis.md) | [next: Native Features](./chapter-07-native-features.md)

## react-hook-form

```bash
npx expo install react-hook-form
```

```typescript
import { useForm, Controller } from "react-hook-form";
import { View, Text, TextInput, Pressable, StyleSheet } from "react-native";

type FormData = { email: string; password: string };

function LoginForm() {
  const { control, handleSubmit, formState: { errors } } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <View style={styles.form}>
      <Controller
        control={control}
        name="email"
        rules={{ required: "Email is required" }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            style={styles.input}
            value={value}
            onChangeText={onChange}
            placeholder="Email"
            keyboardType="email-address"
            autoCapitalize="none"
          />
        )}
      />
      {errors.email && <Text style={styles.error}>{errors.email.message}</Text>}

      <Controller
        control={control}
        name="password"
        rules={{ required: "Password is required", minLength: { value: 8, message: "Min 8 chars" } }}
        render={({ field: { onChange, value } }) => (
          <TextInput
            style={styles.input}
            value={value}
            onChangeText={onChange}
            placeholder="Password"
            secureTextEntry
          />
        )}
      />
      {errors.password && <Text style={styles.error}>{errors.password.message}</Text>}

      <Pressable onPress={handleSubmit(onSubmit)} style={styles.btn}>
        <Text style={styles.btnText}>Login</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  form: { padding: 16, gap: 12 },
  input: { borderWidth: 1, borderColor: "#ccc", borderRadius: 8, padding: 12, fontSize: 16 },
  error: { color: "red", fontSize: 12 },
  btn: { backgroundColor: "#007AFF", padding: 14, borderRadius: 8, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "bold", fontSize: 16 },
});
```

## Validation with zod

```bash
npx expo install zod @hookform/resolvers
```

```typescript
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

const signupSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    email: z.string().email("Invalid email"),
    password: z.string().min(8, "Min 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  });

type SignupData = z.infer<typeof signupSchema>;

function SignupForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupData>({
    resolver: zodResolver(signupSchema),
  });

  const onSubmit = (data: SignupData) => console.log(data);
  // ... render Controllers as above
}
```

## Keyboard Handling

```typescript
import { KeyboardAvoidingView, Platform, ScrollView } from "react-native";

function FormScreen() {
  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={Platform.OS === "ios" ? 64 : 0}
    >
      <ScrollView contentContainerStyle={{ padding: 16 }}>
        {/* Form fields here */}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
```

Dismiss keyboard on tap outside:

```typescript
import { Keyboard, TouchableWithoutFeedback, View } from "react-native";

function DismissKeyboard({ children }: { children: React.ReactNode }) {
  return (
    <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
      <View style={{ flex: 1 }}>{children}</View>
    </TouchableWithoutFeedback>
  );
}
```

## Pickers

### Dropdown Picker

```bash
npx expo install @react-native-picker/picker
```

```typescript
import { Picker } from "@react-native-picker/picker";
import { useState } from "react";
import { View } from "react-native";

function CategoryPicker() {
  const [category, setCategory] = useState("general");
  return (
    <View style={{ borderWidth: 1, borderColor: "#ccc", borderRadius: 8 }}>
      <Picker selectedValue={category} onValueChange={setCategory}>
        <Picker.Item label="General" value="general" />
        <Picker.Item label="Tech" value="tech" />
        <Picker.Item label="Science" value="science" />
      </Picker>
    </View>
  );
}
```

### Date Picker

```bash
npx expo install @react-native-community/datetimepicker
```

```typescript
import DateTimePicker from "@react-native-community/datetimepicker";
import { useState } from "react";
import { View, Pressable, Text, Platform } from "react-native";

function DateSelector() {
  const [date, setDate] = useState(new Date());
  const [show, setShow] = useState(false);

  return (
    <View>
      <Pressable onPress={() => setShow(true)}>
        <Text>{date.toLocaleDateString()}</Text>
      </Pressable>
      {show && (
        <DateTimePicker
          value={date}
          mode="date"
          onChange={(_, selected) => {
            setShow(Platform.OS === "ios");
            if (selected) setDate(selected);
          }}
        />
      )}
    </View>
  );
}
```

## Image Picker

```bash
npx expo install expo-image-picker
```

```typescript
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import { View, Image, Pressable, Text, StyleSheet } from "react-native";

function AvatarPicker() {
  const [image, setImage] = useState<string | null>(null);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.8,
    });
    if (!result.canceled) setImage(result.assets[0].uri);
  };

  return (
    <View style={styles.container}>
      {image && <Image source={{ uri: image }} style={styles.avatar} />}
      <Pressable onPress={pickImage} style={styles.btn}>
        <Text style={styles.btnText}>Pick Photo</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: "center", gap: 16 },
  avatar: { width: 120, height: 120, borderRadius: 60 },
  btn: { padding: 12, backgroundColor: "#007AFF", borderRadius: 8 },
  btnText: { color: "#fff" },
});
```

## Camera Access

```bash
npx expo install expo-camera
```

```typescript
import { CameraView, useCameraPermissions } from "expo-camera";
import { useState, useRef } from "react";
import { View, Pressable, Text, StyleSheet } from "react-native";

function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  if (!permission?.granted) {
    return (
      <View style={styles.container}>
        <Text>Camera permission required</Text>
        <Pressable onPress={requestPermission} style={styles.btn}>
          <Text style={styles.btnText}>Grant Permission</Text>
        </Pressable>
      </View>
    );
  }

  const takePicture = async () => {
    const photo = await cameraRef.current?.takePictureAsync();
    console.log(photo?.uri);
  };

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing="back" />
      <Pressable onPress={takePicture} style={styles.btn}>
        <Text style={styles.btnText}>Snap</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  camera: { width: "100%", height: 400 },
  btn: { marginTop: 16, padding: 12, backgroundColor: "#007AFF", borderRadius: 8 },
  btnText: { color: "#fff", fontWeight: "bold" },
});
```

## Summary

- react-hook-form + zod for type-safe, validated forms
- `KeyboardAvoidingView` prevents the keyboard from covering inputs
- Use community pickers for dropdowns and dates
- expo-image-picker for gallery access, expo-camera for camera

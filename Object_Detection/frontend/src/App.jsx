import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [message, setMessage] = useState("");
  const [filePath, setFilePath] = useState("");
  const [outputData, setOutputData] = useState([]); // State to store the output data
  const[img, setImg]=useState(null);

  // Handle image selection
  const handleImageChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedImage(event.target.files[0]);
    }
  };

  // Handle form submission
  const handleUpload = async () => {
    if (!selectedImage) {
      alert("Please select an image first!");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedImage); // Match the backend key

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload-image/",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      console.log(response.data);
      
      setMessage(response.data.message);
      setFilePath(response.data.file_path);
      setOutputData(response.data.output); // Store the output data in state
      setImg(response.data.other_image);
    } catch (error) {
      console.error("Error uploading image:", error);
      alert("Failed to upload the image!");
    }
  };

  return (
    <div className="main">
      <h1>Image Upload and Object Detection</h1>

      {/* File input */}
      <div className="upload-form">
      <input type="file" accept="image/*" onChange={handleImageChange} />
      <button onClick={handleUpload} style={{ marginLeft: "10px" }}>
        Upload
      </button>
      </div>

      {/* Message */}
      {message && (
        <div style={{ marginTop: "20px" }}>
          <h3>{message}</h3>
          {/* {filePath && <p>File saved at: {filePath}</p>} */}
        </div>
      )}

      {/* Table to display object detection data */}
      {outputData.length > 0 && (
        <table
          border="1"
          style={{
            marginTop: "20px",
            width: "50%",
            textAlign: "left",
            borderCollapse: "collapse",
          }}
        >
          <thead>
            <tr>
              <th>Object</th>
              <th>Confidence</th>
              <th>Box Dimensions</th>
            </tr>
          </thead>
          <tbody>
            {outputData.map((item, index) => (
              <tr key={index}>
                <td>{item.object}</td>
                <td>{(item.confidence * 100).toFixed(2)}%</td>
                <td>{item.box_dimention.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {img &&  <img
            src={`data:image/jpeg;base64,${img}`}
            alt="Processed"
            className="img-final"
          />}

     
    </div>
  );
};

export default App;

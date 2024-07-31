body {margin:0;
    background: white; background-image: url("");
    margin: auto;width.responsive; color: white;
   }
   .city {margin:0;
    background: white; background-image: url("");
    margin: auto;width.responsive; color: black;
   }
   
   .footer {
      color: black;
      background:  #fff;
      height: 100px;
      background-image: url("");
      font-family: italic,Open Sans,italic;
      margin: 10px;
      padding: 0px;
      max-width:100%;
      width.responsive;
      font-size: 17px;
      border: 0px solid red;
   }
   .header {
     background:  #fff;
   height: 60px;
    background-image: url("");
    font-family: italic,Open Sans,italic;
   margin: 10px;
    padding: 0px;
    max-width:100%;
   width.responsive;
     font-size: 17px;
    border: 0px solid red;
   }
   
   .art-container {
       margin: 20px;
       border: 1px solid #ccc;
       padding: 100px;
       position: relative;
   }
   
   .art {
       display: flex;
       flex-direction: column;
   }
   
   .open-slider {
       margin-top: 20px;
       cursor: pointer;
       background-color: #ff;
       color: #fff;
       border: none;
       padding: 5px 10px;
       border-radius: 5px;
   }
   
   .slider {
       position: fixed;
       top: 0; /* Adjust this value to position the slider within the post content */
       right: -75%;
       height: 100%;
       width: 75%;
       background-color: #fff;
       z-index: 1;
       transition: right 0.3s ease-in-out;
       overflow-y: auto;
   }
   
   .slider-content {
       padding: 20px;
   }
   
   .close-slider {
       position: absolute;
       top: 50px;
       right: 10px;
       cursor: pointer;
       background-color: #ff4136;
       color: #fff;
       border: none;
       padding: 5px 10px;
       border-radius: 5px;
   }
   
   .topnav {  overflow: hidden;
    background-color: #2F2F2F;
    max-width: 100%;
   }
   .topnav a { float: left; display: block;
    color: white;
   text-align: center;
   padding: 11px 13px;
   text-decoration: none;font-size: 21px;
   }
   .topnav a:hover {background-color: #ddd;
   color: black;
   }
   .topnav .icon {
     display: none;
   }
   
   @media screen and (max-width: 600px) {
     .topnav a:not(:first-child) {display: none;}
     .topnav a.icon {
       float: right;
       display: block;
     }
   }
   
   @media screen and (max-width: 600px) {
     .topnav.responsive {position: relative;}
     .topnav.responsive .icon {
       position: absolute;
       right: 0;
       top: 0;
     }
   }
     .topnav.responsive a {
       float: none;
       display: block;
       text-align: left;
     }
   
   }.videoWrapper {
      position: relative;
      padding-bottom: 56.25%; /* 16:9 */
      padding-top: 25px;
      height: 0;
   }
   .videoWrapper iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
   }img {
       max-width: 100%; /* or any custom size */
       height: auto; 
       object-fit: contain;
       text-align:center;
   }#textboxid
   {
       height:14px;
       font-size:12pt;border: 2px solid red;
   }
   
   .row:after { 
   content: "";
    Display: table;
    clear: both;
   }
   .container {
    width: 100%;
}

.row {
    display: flex;
    margin-bottom: 10px; /* Space between rows */
}

.three-columns .column {
    flex: 1; /* Equal width for all three columns */
    background-color: white
    padding: 10px;
    margin: 2px;
}

.two-blocks .block {
    padding: 10px;
    margin: 2px;
}

.two-blocks .large {
    flex: 1; /* Larger block takes more space */
    background-color: white
    
}

.two-blocks .small {
    flex: 1; /* Smaller block takes less space */
    background-color: white;
}

@media (max-width: 600px) {
    .row {
        flex-direction: column;
    }
}
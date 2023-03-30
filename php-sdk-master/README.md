# Unitpay PHP SDK

PHP SDK for [Unitpay.ru](https://unitpay.ru).

Documentation https://help.unitpay.ru

## Examples ##

These are just some quick examples. Check out the samples
in [`/examples`](https://github.com/unitpay/php-sdk/blob/master/examples).

### Payment integration using Unitpay form

```php
<?php
include ('../UnitPay.php');

// Project Data
$domain = 'unitpay.ru';// Your working domain: unitpay.ru or address provided by unitpay support service
$secretKey  = '9e977d0c0e1bc8f5cc9775a8cc8744f1';// Project secret key
$publicId   = '15155-ae12d';

// My item Info
$itemName = 'Iphone 6 Skin Cover';

// My Order Data
$orderId        = 'a183f94-1434-1e44';
$orderSum       = 900;
$orderDesc      = 'Payment for item "' . $itemName . '"';
$orderCurrency  = 'RUB';

$unitpay = new UnitPay($domain, $secretKey);

$unitpay
    ->setBackUrl('https://domain.com')
    ->setCustomerEmail('customer@domain.com')
    ->setCustomerPhone('79001235555')
    ->setCashItems([
       new CashItem($itemName, 1, $orderSum) 
    ]);

$redirectUrl = $unitpay->form(
    $publicId,
    $orderSum,
    $orderId,
    $orderDesc,
    $orderCurrency
);

header("Location: " . $redirectUrl);
```

### Payment integration using Unitpay API

```php
<?php

header('Content-Type: text/html; charset=UTF-8');

/**
 * API integration
 *
 * @link https://help.unitpay.ru/payments/create-payment
 */

include ('../UnitPay.php');

// Project Data
$domain = 'unitpay.ru';// Your working domain: unitpay.ru or address provided by unitpay support service
$projectId  = 1;
$secretKey  = '9e977d0c0e1bc8f5cc9775a8cc8744f1';// Project secret key

// My item Info
$itemName = 'Iphone 6 Skin Cover';

// My Order Data
$orderId        = 'a183f94-1434-1e44';
$orderSum       = 900;
$orderDesc      = 'Payment for item "'.$itemName.'"';
$orderCurrency  = 'RUB';

$unitpay = new UnitPay($domain, $secretKey);

/**
 * Base params: account, desc, sum, currency, projectId, paymentType
 * Additional params:
 *  Qiwi, Mc:
 *      phone
 * alfaClick:
 *      clientId
 *
 * @link https://help.unitpay.ru/payments/create-payment
 */
$response = $unitpay->api('initPayment', [
    'account'     => $orderId,
    'desc'        => $orderDesc,
    'sum'         => $orderSum,
    'paymentType' => 'yandex',
    'currency'    => $orderCurrency,
    'projectId'   => $projectId
]);

// If need user redirect on Payment Gate
if (isset($response->result->type)
    && $response->result->type == 'redirect') {
    // Url on PaymentGate
    $redirectUrl = $response->result->redirectUrl;
    // Payment ID in Unitpay (you can save it)
    $paymentId = $response->result->paymentId;
    // User redirect
    header("Location: " . $redirectUrl);

// If without redirect (invoice)
} elseif (isset($response->result->type)
    && $response->result->type == 'invoice') {
    // Url on receipt page in Unitpay
    $receiptUrl = $response->result->receiptUrl;
    // Payment ID in Unitpay (you can save it)
    $paymentId = $response->result->paymentId;
    // Invoice Id in Payment Gate (you can save it)
    $invoiceId = $response->result->invoiceId;
    // User redirect
    header("Location: " . $receiptUrl);

// If error during api request
} elseif (isset($response->error->message)) {
    $error = $response->error->message;
    print 'Error: '.$error;
}
```

### Handler sample

```php
<?php

/**
 *  Demo handler for your projects
 *
 */
include ('../UnitPay.php');

// Project Data
$domain = 'unitpay.ru';// Your working domain: unitpay.ru or address provided by unitpay support service
$projectId  = 1;
$secretKey  = '9e977d0c0e1bc8f5cc9775a8cc8744f1';// Project secret key

// My item Info
$itemName = 'Iphone 6 Skin Cover';

// My Order Data
$orderId        = 'a183f94-1434-1e44';
$orderSum       = 900;
$orderDesc      = 'Payment for item "' . $itemName . '"';
$orderCurrency  = 'RUB';

$unitpay = new UnitPay($domain, $secretKey);

try {
    // Validate request (check ip address, signature and etc)
    $unitpay->checkHandlerRequest();

    list($method, $params) = [$_GET['method'], $_GET['params']];

    // Very important! Validate request with your order data, before complete order
    if (
        $params['orderSum'] != $orderSum ||
        $params['orderCurrency'] != $orderCurrency ||
        $params['account'] != $orderId ||
        $params['projectId'] != $projectId
    ) {
        // logging data and throw exception
        throw new InvalidArgumentException('Order validation Error!');
    }
    switch ($method) {
        // Just check order (check server status, check order in DB and etc)
        case 'check':
            echo $unitpay->getSuccessHandlerResponse('Check Success. Ready to pay.');
            break;
        // Method Pay means that the money received
        case 'pay':
            // Please complete order
            echo $unitpay->getSuccessHandlerResponse('Pay Success');
            break;
        // Method Error means that an error has occurred.
        case 'error':
            // Please log error text.
            echo $unitpay->getSuccessHandlerResponse('Error logged');
            break;
    }
// Oops! Something went wrong.
} catch (Exception $e) {
    echo $unitpay->getErrorHandlerResponse($e->getMessage());
}
```

## Installation

### Install composer package
Set up `composer.json` in your project directory:
```
{
  "require":{"unitpay/php-sdk":"dev-master"}
}
```

Run [composer](https://getcomposer.org/doc/00-intro.md#installation):
```sh
$ php composer.phar install
```

### Direct download

Download [latest version](https://github.com/unitpay/php-sdk/archive/master.zip), unzip and copy to your project folder.

## Contributing ##

Please feel free to contribute to this project! Pull requests and feature requests welcome!
